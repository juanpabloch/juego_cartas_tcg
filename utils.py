def instance_id_generator():
    count = 1
    while True:
        yield f"card_{count:04d}"
        count += 1


generate_instance_id = instance_id_generator()