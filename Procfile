worker: python -c "
import time, subprocess
while True:
    subprocess.run(['python', 'update_scores.py'])
    print('Prochaine mise à jour dans 60 minutes...')
    time.sleep(3600)
"
