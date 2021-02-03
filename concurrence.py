import subprocess
import io
import time


worklist = ['python scraper.py', 'python match.py']

child_processes = []
for work in worklist:
    p = subprocess.Popen(work.split())
    child_processes.append(p)

# now you can join them together
start = time.time()
for cp in child_processes:
    cp.wait()
end = time.time()
print(end - start)
