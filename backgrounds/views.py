from django.shortcuts import render
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from .forms import GridForm, DotForm
from .models import GameBoard, UserPath, PathsOnBoard
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
import json, time
from django.http import JsonResponse, StreamingHttpResponse
from threading import Lock
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your views here.

_events: list[str] = []
_lock = Lock()

def _enqueue(event: str):
    with _lock:
        _events.append(event)


@login_required
def create_grid(request):
    if request.method == "POST":
        grid_form = GridForm(request.POST)
        if grid_form.is_valid():
            # Create the grid for the current user
            grid_name = grid_form.cleaned_data['name']
            rows = grid_form.cleaned_data['rows']
            cols = grid_form.cleaned_data['cols']
            
            # Add dots to the grid
            dots = []

            # Save the grid and dots to the database
            grid = GameBoard.objects.create(
                user=request.user,
                title=grid_name,
                rows=rows,
                cols=cols,
                dots=dots
            )
            return redirect('')  # Redirect to homepage (as defined in main/urls.py)
    else:
        grid_form = GridForm()
    return render(request, 'backgrounds/create_grid.html', {
        'grid_form': grid_form,
    })

@login_required
def edit_grid(request, grid_id):
    grid = get_object_or_404(GameBoard, id=grid_id, user=request.user)
    DotsFormSet = formset_factory(DotForm, extra=1)
    if request.method == "POST":
        dots_formset = DotsFormSet(request.POST)
        if dots_formset.is_valid():
            # Save the dots to the grid
            new_dots = []
            for form in dots_formset:
                if form.cleaned_data:
                    dot_data = form.cleaned_data  # e.g. {'row': 1, 'col': 2, 'color': '#FF0000'}
                    new_dots.append(dot_data)
            grid.dots = new_dots
            try:
                grid.save()
                return redirect('')  # Redirect to your desired URL
            except ValidationError as e:
                error = e.messages
                # Re-render with error message for the user
                return render(request, 'backgrounds/edit_grid.html', {
                    'grid': grid,
                    'dots_formset': dots_formset,
                    'error': error,
                })
    else:
        dots_formset = DotsFormSet(initial=grid.dots)
    return render(request, 'backgrounds/edit_grid.html', {
        'grid': grid,
        'dots_formset': dots_formset,
    })

@login_required
def list_grids(request):
    grids = GameBoard.objects.filter()
    paths = PathsOnBoard.objects.filter(user=request.user)
    return render(request, 'backgrounds/list_grids.html', {
        'grids': grids,
        'paths': paths,
    })

@login_required
def make_paths_on_grid(request, grid_id):
    grid = get_object_or_404(GameBoard, id=grid_id)
    paths = UserPath.objects.filter(board=grid)
    used_dots = []
    for path in paths:
        if path.starting_dot:
            used_dots.append(path.starting_dot)
        if path.finishing_dot:
            used_dots.append(path.finishing_dot)
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = json.loads(request.body)
        paths_data = data.get("paths", [])
        user_paths = []
        for path in paths_data:
            user_path = UserPath.objects.create(
                user=request.user,
                board=grid,
                starting_dot=path.get("starting_dot"),
                finishing_dot=path.get("finishing_dot"),
                path_points=path.get("path_points", [])
            )
            user_paths.append(user_path)
        paths_on_board = PathsOnBoard.objects.create(user=request.user, board=grid)
        paths_on_board.paths.set(user_paths)
        return JsonResponse({"status": "ok", "paths_on_board_id": paths_on_board.id})

    return render(request, 'backgrounds/make_paths_on_grid.html', {
        'grid': grid,
        'dots': grid.dots,
        'paths': list(paths),
        'used_dots': used_dots,
    })


@login_required
def show_paths_on_grid(request, grid_id, path_id):
    grid = get_object_or_404(GameBoard, id=grid_id)
    paths_on_board = get_object_or_404(PathsOnBoard, id=path_id, board=grid)

    # Build lookup dict keyed by "row,col"
    point_lookup = {}
    for path in paths_on_board.paths.all():
        if path.starting_dot:
            key = f"{path.starting_dot['row']},{path.starting_dot['col']}"
            point_lookup[key] = path.starting_dot
        if path.finishing_dot:
            key = f"{path.finishing_dot['row']},{path.finishing_dot['col']}"
            point_lookup[key] = path.finishing_dot
        for point in path.path_points:
            key = f"{point['row']},{point['col']}"
            point_lookup[key] = point

    # Create grid_cells as a list of rows, each a list of cells
    grid_cells = []
    for i in range(grid.rows):
        row = []
        for j in range(grid.cols):
            cell = point_lookup.get(f"{i},{j}")  # Could be None or dict with 'color'
            row.append(cell)
        grid_cells.append(row)

    return render(request, 'backgrounds/show_paths_on_grid.html', {
        'grid': grid,
        'paths_on_board': paths_on_board,
        'grid_cells': grid_cells,
    })


def sse_notifications(request):
    def event_stream():
        while True:
            with _lock:
                if _events:
                    yield _events.pop(0)
                    continue

            yield 'keep-alive\n\n'
            time.sleep(15)

    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )


@receiver(post_save, sender=GameBoard)
def on_new_board(sender, instance: GameBoard, created, **kwargs):
    if not created:
        return
    payload = {
        "board_id": instance.id,
        "board_name": instance.title,
        "creator_username": instance.user.username
    }
    msg = f"event: newBoard\ndata: {json.dumps(payload)}\n\n"
    _enqueue(msg)

@receiver(post_save, sender=PathsOnBoard)
def on_new_paths_on_board(sender, instance: PathsOnBoard, created, **kwargs):
    if not created:
        return
    payload = {
        "paths_on_board_id": instance.id,
        "board_id": instance.board.id,
        "user_username": instance.user.username
    }
    msg = f"event: newPathsOnBoard\ndata: {json.dumps(payload)}\n\n"
    _enqueue(msg)