import subprocess
import atexit
import signal

def cleanup():
    # for p in processes:
    #     p.terminate()
    print("cleaned up")


if __name__ == '__main__':
    procs = []

    # subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe C:/Users/Felix/IdeaProjects/Macro/tests/mp_shared_mem/proc_a.py")
    # subprocess.Popen(r"C:\Users\Felix\.virtualenvs\Macro\Scripts\python.exe C:/Users/Felix/IdeaProjects/Macro/tests/mp_shared_mem/proc_b.py")

    # atexit.register(cleanup, procs)
    atexit.register(cleanup)
    # signal.signal(signal.SIGTERM,cleanup)
    # signal.signal(signal.SIGINT,cleanup)

    while True:
        print("a")


