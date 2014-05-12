c = get_config()

# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always

# Notebook config
#c.NotebookApp.certfile = u'/absolute/path/to/your/certificate/mycert.pem'
#c.NotebookApp.ip = '${server:host}'
c.NotebookApp.ip = 127.0.0.1
c.NotebookApp.open_browser = False
#c.NotebookApp.password = u'sha1:bcd259ccf...[your hashed password here]'
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = ${ports:ipython}
# Running with a different URL prefix
c.NotebookApp.base_project_url = '/ipython/'
c.NotebookApp.base_kernel_url = '/ipython/'
c.NotebookApp.base_url = '/ipython/'
c.NotebookApp.trust_xheaders = True
c.NotebookApp.webapp_settings = {'static_url_prefix':'/ipython/static/'}

