from google.colab import drive
import subprocess
import sys
import importlib
import tensorflow as tf

def run_shell(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    sys.stdout.write(res.stdout)
    return res

def mount_drive(path):
    drive.mount(path)

def register_git_ssh_key(ssh_path, email, user_name):
    run_shell("rm -rf /root/.ssh/")
    run_shell("cp -r {} /root/.ssh".format(ssh_path))
    run_shell("chmod 700 /root/.ssh")
    run_shell("ssh-keyscan github.com >> /root/.ssh/known_hosts")
    run_shell("chmod 644 /root/.ssh/known_hosts")
    run_shell("git config --global user.email {}".format(email))
    run_shell("git config --global user.name {}".format(user_name))


def git(repo_path, command):
    run_shell("git -C {} {}".format(repo_path, command))

# reload modules
def reloads(modules, globals):
    if type(modules) == str:
        modules = [x.strip() for x in modules.split(',')]
    for module in modules:
        reload(module, globals)

def reload(module, globals):
    if type(module) == str:
        importlib.import_module(module)
        module = sys.modules[module]
    importlib.reload(module)
    funcs = [func for func in dir(module) if not func.startswith('__')]
    for func_name in funcs:
        globals()[func_name] = module.__dict__[func_name]

# save/load from buckets
def is_exist_in_bucket(*fnames):
    fname = os.path.join(*fnames)
    res = run_shell("gsutil -q stat {}".format(fname))
    return res.returncode == 0

def save_to_bucket(bucket_dir, fname):
  tf.gfile.MakeDirs(bucket_dir)
  bucket_fname = os.path.join(bucket_dir, fname)
  run_shell("gsutil cp {} {}".format(fname, bucket_fname))

def load_from_bucket(bucket_dir, fname):
  bucket_fname = os.path.join(bucket_dir, fname)
  run_shell("gsutil cp {} {}".format(bucket_fname,fname))

def load_or_execute(bucket_dir, fname, func, force_execution = False, *args, **kwargs):
    if force_execution or not is_exist_in_bucket(bucket_dir,fname):
        func(args, kwargs)
        save_to_bucket(bucket_dir,fname)
    else:
        load_from_bucket(bucket_dir,fname)