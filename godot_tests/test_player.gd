extends SceneTree
func _init():
	var root = load("res://maps/nuketown/Nuketown.tscn").instantiate()
	get_root().add_child(root)
	await physics_frame
	await physics_frame
	var fails := 0
	for team in ["TeamA", "TeamB"]:
		for m in root.get_node("SpawnPoints/" + team).get_children():
			var pl = CharacterBody3D.new()
			var cs = CollisionShape3D.new(); var cap = CapsuleShape3D.new(); cap.radius = 0.4; cap.height = 1.8; cs.shape = cap
			pl.add_child(cs); root.add_child(pl)
			pl.global_position = m.global_position + Vector3(0, 1.0, 0)
			var start_y = pl.global_position.y
			for i in range(90):
				pl.velocity.y -= 9.8 / 60.0 * 1.0
				pl.move_and_slide()
				await physics_frame
			var ok = pl.is_on_floor() and pl.global_position.y > start_y - 3.0
			# horizontal walk test: 8 directions for 25m, record max distance and min y
			var res = []
			for d in range(0, 8, 2):
				var dir = Vector3(cos(d * PI / 4), 0, sin(d * PI / 4))
				var p0 = pl.global_position
				var minY = p0.y
				for i in range(100):
					pl.velocity = dir * 9.0 + Vector3(0, pl.velocity.y - 9.8/60.0, 0)
					pl.move_and_slide(); await physics_frame
					minY = min(minY, pl.global_position.y)
				var dist = Vector2(pl.global_position.x - p0.x, pl.global_position.z - p0.z).length()
				res.append("%.0f/%.1f" % [dist, pl.global_position.y - p0.y])
				pl.global_position = p0; pl.velocity = Vector3.ZERO
				for i in range(10): pl.move_and_slide(); await physics_frame
			print(m.name, " floor_ok=", ok, " y=%.2f" % pl.global_position.y, " 8dir walk dist(25m max)/dy: ", res)
			if not ok: fails += 1
			pl.queue_free()
	print("FAILS=", fails)
	quit(0)
