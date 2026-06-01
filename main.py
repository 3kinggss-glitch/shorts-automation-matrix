def assemble_and_publish():
    # 1. Create a "lock file" name for today
    lock_file = f"api_lock_{datetime.date.today()}.txt"
    
    # 2. Check if we already failed today
    if os.path.exists(lock_file):
        print("🛑 API limit already hit today. Skipping run to save quota.")
        return

    try:
        # ... [Your existing script generation and upload code] ...
        script, state = generate_viral_script()
        # ... (rest of your successful logic)
        
    except Exception as e:
        # 3. If we hit a quota error, create the lock file 
        # so we don't try again until tomorrow
        if "429" in str(e) or "Quota exceeded" in str(e):
            with open(lock_file, "w") as f:
                f.write("failed")
        raise e
