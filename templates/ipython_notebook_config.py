c = get_config()

# Kernel config
c.IPKernelApp.pylab = 'inline'  # if you want plotting support always

# Notebook config
#c.NotebookApp.certfile = u'/absolute/path/to/your/certificate/mycert.pem'
c.NotebookApp.ip = '127.0.0.1'
c.NotebookApp.open_browser = False
#c.NotebookApp.password = u'sha1:bcd259ccf...[your hashed password here]'
c.NotebookApp.password =  ${settings:ipython-password}
# It is a good idea to put it on a known, fixed port
c.NotebookApp.port = ${settings:ipython-port}
# Running with a different URL prefix
c.NotebookApp.base_project_url = '/ipython/notebook/'
c.NotebookApp.base_kernel_url = '/ipython/notebook/'
c.NotebookApp.base_url = '/ipython/notebook/'
c.NotebookApp.trust_xheaders = True
c.NotebookApp.webapp_settings = {'static_url_prefix':'/ipython/notebook/static/'}

