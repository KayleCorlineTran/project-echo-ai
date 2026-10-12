def inspect_object(game_state, object_name):

    object_name = object_name.lower().strip()

    # =========================
    # LABORATORY
    # =========================

    if game_state.current_room == "laboratory":

        if "bàn" in object_name:
            clue = "Mã ghi trên tờ giấy: 4-1-3-2"
            game_state.add_clue(clue)

            return {
                "success": True,
                "message": (
                    "Bạn kiểm tra chiếc bàn. "
                    "Bên dưới một quyển sổ cũ là tờ giấy ghi: 4-1-3-2."
                )
            }

        if "tủ" in object_name:
            if not game_state.has_item("silver_key"):
                game_state.add_item("silver_key")

                return {
                    "success": True,
                    "message": (
                        "Trong ngăn tủ, bạn tìm thấy một chiếc chìa khóa bạc."
                    )
                }

            return {
                "success": True,
                "message": "Chiếc tủ không còn gì đáng chú ý."
            }

        if "két" in object_name:
            if game_state.flags["safe_opened"]:
                return {
                    "success": True,
                    "message": "Chiếc két đã được mở."
                }

            return {
                "success": False,
                "message": "Chiếc két cần một mã gồm 4 chữ số."
            }


    return {
        "success": False,
        "message": "Bạn không tìm thấy gì đặc biệt."
    }


def use_code(game_state, code):

    code = code.strip()

    if game_state.current_room == "laboratory":

        if code == "4132":

            if game_state.flags["safe_opened"]:
                return {
                    "success": True,
                    "message": "Chiếc két đã được mở trước đó."
                }

            game_state.set_flag("safe_opened", True)

            game_state.add_item("access_card")

            game_state.solve_puzzle("laboratory_safe")

            return {
                "success": True,
                "message": (
                    "Bạn nhập 4132. "
                    "Chiếc két bật mở. "
                    "Bên trong có một thẻ truy cập."
                )
            }

        return {
            "success": False,
            "message": "Mã không đúng."
        }


def move_room(game_state, room_name):

    room_name = room_name.lower().strip()

    # Laboratory → Library
    if room_name == "library":

        game_state.current_room = "library"

        return {
            "success": True,
            "message": (
                "Bạn bước vào thư viện tối. "
                "Những kệ sách cao phủ đầy bụi."
            )
        }

    # Library → Generator room
    if room_name == "generator":

        if not game_state.has_item("silver_key"):

            return {
                "success": False,
                "message": (
                    "Cánh cửa phòng máy bị khóa. "
                    "Bạn cần một chiếc chìa khóa."
                )
            }

        game_state.current_room = "generator"

        return {
            "success": True,
            "message": (
                "Chiếc chìa khóa bạc mở cửa phòng máy."
            )
        }

    # Generator → Control room
    if room_name == "control":

        if not game_state.has_item("access_card"):

            return {
                "success": False,
                "message": (
                    "Cửa phòng điều khiển yêu cầu thẻ truy cập."
                )
            }

        game_state.current_room = "control"

        return {
            "success": True,
            "message": (
                "Thẻ truy cập được chấp nhận. "
                "Cửa phòng điều khiển mở ra."
            )
        }

    return {
        "success": False,
        "message": "Bạn không thể đi tới đó."
    }
