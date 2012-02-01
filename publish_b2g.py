import ConfigParser
import datetime
import os
import shutil
import subprocess
import sys

from mozillapulse.config import PulseConfiguration
from mozillapulse.messages.base import GenericMessage
from mozillapulse.publishers import GenericPublisher

class B2GPulsePublisher(GenericPublisher):
    def __init__(self, **kwargs):
        super(B2GPulsePublisher, self).__init__(PulseConfiguration(**kwargs),
                                                'org.mozilla.exchange.b2g')

def publish_build(commit, filename):
    publisher = B2GPulsePublisher()
    msg = GenericMessage()
    msg.routing_parts = ['b2g', 'qemu', 'build', 'available']
    msg.set_data('buildurl', 'http://builder.boot2gecko.org/%s' % os.path.basename(filename))
    msg.set_data('commit', commit)
    publisher.publish(msg)

def clean_old_builds(outdir):
    # delete builds in the output dir > 2 days old
    for afile in os.listdir(outdir):
        stat = os.stat(os.path.join(outdir, afile))
        if (datetime.datetime.now() - 
            datetime.datetime.fromtimestamp(stat.st_mtime) > 
            datetime.timedelta(days=2)):
            print 'removing old file', afile
            os.remove(os.path.join(outdir, afile))

if __name__ == '__main__':
    args = sys.argv[1:]

    cfg = ConfigParser.ConfigParser()
    if args:
        cfg.read(args[0])
    else:
        cfg.read(os.path.join(os.path.dirname(__file__), 'default.conf'))
    print 'using config', cfg.items('build')

    repodir = cfg.get('build', 'repo_dir')
    infile = cfg.get('build', 'in_filename')
    indir = cfg.get('build', 'in_dir')
    outfile = cfg.get('build', 'out_filename')
    outdir = cfg.get('build', 'out_dir')

    clean_old_builds(outdir)

    proc = subprocess.Popen(['git', 'rev-list', '--max-count=1', 'HEAD'],
                            stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                            cwd=repodir)
    retcode = proc.wait()
    commit = proc.stdout.read().strip()
    filename = outfile % commit
    shutil.copyfile(os.path.join(indir, infile), os.path.join(outdir, filename))
    publish_build(commit, filename)

