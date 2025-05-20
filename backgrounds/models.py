from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.

class BackgroundImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds/')

    def __str__(self):
        return self.name
    
class GameBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gameboards')
    title = models.CharField(max_length=100)
    rows = models.IntegerField()
    cols = models.IntegerField()
    dots = models.JSONField(default=list, blank=True ,help_text="List of dots, e.g., [{'row': 1, 'col': 2, 'color': '#FF0000'}]")

    def clean(self):
        dot_positions = set()
        color_counts = {}
        for dot in self.dots:
            row = dot.get("row")
            col = dot.get("col")
            color = dot.get("color")
            if row is None or col is None:
                continue
            # Check bounds
            if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                raise ValidationError(
                    f"Dot at row {row} and col {col} is out of grid bounds."
                )
            # Check for duplicates
            if (row, col) in dot_positions:
                raise ValidationError(
                    f"Duplicate dot found at position row {row} and col {col}."
                )
            dot_positions.add((row, col))
            color_counts[color] = color_counts.get(color, 0) + 1
        for color, count in color_counts.items():
            if count != 2 and count != 0:
                raise ValidationError(
                    f"Color {color} must be used for exactly 2 dots (currently {count})."
                )
    def save(self, *args, **kwargs):
        self.full_clean()  # This calls clean() and runs validations before saving.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class UserPath(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE)
    starting_dot = models.JSONField(default=dict, blank=True, help_text="Starting dot position, e.g., {'row': 1, 'col': 2, 'color': '#FF0000'}")
    finishing_dot = models.JSONField(default=dict, blank=True, help_text="Finishing dot position, e.g., {'row': 3, 'col': 4, 'color': '#00FF00'}")
    path_points = models.JSONField(default=list, blank=True, help_text="List of path points, e.g., [{'row': 1, 'col': 2, 'color': '#FF0000'}, {'row': 2, 'col': 3, 'color': '#00FF00'}]")

    def clean(self):
        start_color = self.starting_dot.get("color")
        finish_color = self.finishing_dot.get("color")
        if start_color != finish_color:
            raise ValidationError("Starting and finishing dots must have the same color.")

        # Check if starting_dot exists in board.dots
        if self.starting_dot and self.starting_dot not in self.board.dots:
            raise ValidationError("Starting dot does not exist on the board.")

        # Check if finishing_dot exists in board.dots
        if self.finishing_dot and self.finishing_dot not in self.board.dots:
            raise ValidationError("Finishing dot does not exist on the board.")

class PathsOnBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE)
    paths = models.ManyToManyField(UserPath, related_name='paths_on_board')

    def clean(self):
        # Collect all path points for each path as a set of (row, col)
        path_point_sets = []
        for path in self.paths.all():
            points = {(pt['row'], pt['col']) for pt in path.path_points}
            path_point_sets.append(points)
        # Check for intersections between any two sets
        for i in range(len(path_point_sets)):
            for j in range(i + 1, len(path_point_sets)):
                if path_point_sets[i].intersection(path_point_sets[j]):
                    raise ValidationError("Two or more paths cross each other on the board.")