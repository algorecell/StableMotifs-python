
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    jupyter_setup("stablemotifs")

    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "load")

else:
    def upload():
        raise NotImplementedError

