extends Node2D


@onready var player = $Player
@onready var ai_request = $AIRequest
@onready var dialogue_frame = $UI/DialogueFrame
@onready var dialogue_label = $UI/DialogueFrame/DialogueLabel


var ai_busy := false


func _ready():
	ai_request.request_completed.connect(_on_ai_response)

	# =========================
	# TEXTBOX
	# =========================

	dialogue_frame.size = Vector2(900, 170)

	var screen_size = get_viewport_rect().size

	dialogue_frame.position = Vector2(
		(screen_size.x - dialogue_frame.size.x) / 2,
		screen_size.y - dialogue_frame.size.y - 20
	)

	dialogue_label.position = Vector2(250, 25)
	dialogue_label.size = Vector2(600, 120)

	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER

	dialogue_label.text = "ECHO: Hệ thống đang chờ."


# =========================
# INPUT
# =========================

func _process(_delta):
	if Input.is_action_just_pressed("interact"):

		if ai_busy:
			return

		var target = get_active_interactable()

		if target != null:
			send_interaction(
				"inspect",
				target.object_name,
				target.interaction_message
			)

		else:
			dialogue_label.text = (
				"Bạn cần đứng gần vật thể để tương tác."
			)
			print_interaction_debug()


# Trả về vật thể gần người chơi nhất trong số các vùng đang đứng trong.
# Nếu hai vùng chồng lên nhau thì chọn vật gần hơn.
func get_active_interactable():
	var best = null
	var best_distance := INF

	for area in get_tree().get_nodes_in_group("interactables"):
		# Hỏi trực tiếp physics thay vì tin vào cờ player_inside
		if not area.overlaps_body(player):
			continue

		var distance = player.global_position.distance_to(
			area.get_center()
		)

		if distance < best_distance:
			best_distance = distance
			best = area

	return best


# In ra tab Output để biết vì sao không tìm thấy vật thể nào
func print_interaction_debug():
	var areas = get_tree().get_nodes_in_group("interactables")

	print("--- INTERACT DEBUG ---")
	print("Player position: ", player.global_position)
	print("Interactables registered: ", areas.size())

	for area in areas:
		print(
			area.name,
			" | object=", area.object_name,
			" | overlaps_player=", area.overlaps_body(player),
			" | monitoring=", area.monitoring,
			" | center=", area.get_center()
		)


# =========================
# SEND REQUEST
# =========================

func send_interaction(
	action: String,
	object_name: String,
	message: String
):
	if ai_busy:
		return

	ai_busy = true

	dialogue_label.text = "ECHO: Đang phân tích..."

	var url = "http://127.0.0.1:8000/interact"

	var payload = {
		"action": action,
		"object": object_name,
		"room": "laboratory",
		"message": message
	}

	var headers = [
		"Content-Type: application/json"
	]

	var request_error = ai_request.request(
		url,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(payload)
	)

	if request_error != OK:
		ai_busy = false

		dialogue_label.text = (
			"ECHO: Không thể gửi yêu cầu đến hệ thống."
		)

		print(
			"HTTPRequest error: ",
			request_error
		)


# =========================
# AI RESPONSE
# =========================

func _on_ai_response(
	result,
	response_code,
	headers,
	body
):
	ai_busy = false

	print("HTTP result: ", result)
	print("HTTP code: ", response_code)

	if response_code != 200:
		dialogue_label.text = (
			"ECHO: Không thể kết nối hệ thống."
		)

		print(
			"AI ERROR: ",
			response_code
		)

		return

	var response_text = body.get_string_from_utf8()

	var data = JSON.parse_string(
		response_text
	)

	if data == null:
		dialogue_label.text = (
			"ECHO: Phản hồi từ AI không hợp lệ."
		)

		print(
			"JSON parse failed: ",
			response_text
		)

		return

	if not data.has("dialogue"):
		dialogue_label.text = (
			"ECHO: Không nhận được nội dung phản hồi."
		)

		return


	# =========================
	# CLEAN DIALOGUE
	# =========================

	var dialogue = str(
		data["dialogue"]
	).strip_edges()


	# Nếu model tự ghi "ECHO:" thì xóa đi
	if dialogue.to_upper().begins_with("ECHO:"):
		dialogue = dialogue.substr(5).strip_edges()

	elif dialogue.to_upper().begins_with("ECHO "):
		dialogue = dialogue.substr(5).strip_edges()


	dialogue_label.text = (
		"ECHO: " + dialogue
	)


	# =========================
	# DEBUG
	# =========================

	print(
		"ECHO: ",
		dialogue
	)

	if data.has("memory_used"):
		print(
			"Memory used: ",
			data["memory_used"]
		)

	if data.has("memory_saved"):
		print(
			"Memory saved: ",
			data["memory_saved"]
		)

	if data.has("state_update"):
		print(
			"State update: ",
			data["state_update"]
		)

	if data.has("game_state"):
		print(
			"Game state: ",
			data["game_state"]
		)
