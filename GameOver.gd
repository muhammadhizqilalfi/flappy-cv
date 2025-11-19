extends CanvasLayer

@export var pipe_scene : PackedScene
var score
signal restart

func gameover(current_score):
	$ScoreLabel.text = "SCORE: " + str(current_score)

func _on_restart_button_pressed():
	restart.emit()
