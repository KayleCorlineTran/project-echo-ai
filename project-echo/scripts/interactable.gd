extends Area2D

@export var object_name := "computer"
@export var interaction_message := "Tôi kiểm tra chiếc máy tính."

var player_inside := false

func _on_body_entered(body):
	if body.name == "Player":
		player_inside = true
		print("Player entered computer area")

func _on_body_exited(body):
	if body.name == "Player":
		player_inside = false
		print("Player exited computer area")
