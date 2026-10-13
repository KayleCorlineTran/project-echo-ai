extends Area2D

# Tên gửi cho backend. Phải khớp key trong OBJECT_CONTEXT ở api.py:
# "computer", "safe", "door"
@export var object_name := "computer"

# Câu "người chơi nói/làm" gửi kèm cho AI
@export_multiline var interaction_message := "Tôi kiểm tra chiếc máy tính."

var player_inside := false


func _ready():
	add_to_group("interactables")

	# Chỉ nối signal nếu trong scene chưa nối, tránh bị nối 2 lần
	if not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)

	if not body_exited.is_connected(_on_body_exited):
		body_exited.connect(_on_body_exited)


# Tâm thật của vùng tương tác (Area2D nằm ở (0,0),
# còn CollisionShape2D mới là phần được dịch chuyển)
func get_center() -> Vector2:
	return $CollisionShape2D.global_position


func _on_body_entered(body):
	if body.name == "Player":
		player_inside = true


func _on_body_exited(body):
	if body.name == "Player":
		player_inside = false
