extends CharacterBody2D

@export var speed := 120.0

@onready var sprite = $AnimatedSprite2D

func _ready():
	global_position = Vector2(533.0, 339.0)

func _physics_process(_delta):
	var direction = Input.get_vector(
		"ui_left",
		"ui_right",
		"ui_up",
        "ui_down"
	)

	velocity = direction * speed

	if direction != Vector2.ZERO:
		sprite.play("walk_down")
	else:
		sprite.stop()

	move_and_slide()
