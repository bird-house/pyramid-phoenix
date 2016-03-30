var uploader = new qq.FineUploader({
  debug: true,
  autoUpload: false,
  element: document.getElementById("fine-uploader"),
  template: 'qq-template',
  request: {
    endpoint: '/upload'
  },
  chunking: {
    enabled: false,
    concurrent: {
      enabled: false
    },
    success: {
      endpoint: "/upload"
    }
  },
  deleteFile: {
    enabled: false,
    endpoint: '/upload'
  },
  resume: {
    enabled: false
  },
  retry: {
    enableAuto: true,
    showButton: true
  },
  thumbnails: {
    placeholders: {
      waitingPath: '${request.static_path("phoenix:static/jquery.fine-uploader/placeholders/waiting-generic.png")}',
      notAvailablePath: '${request.static_path("phoenix:static/jquery.fine-uploader/placeholders/not_available-generic.png")}'
    }
  },
  validation: {
    allowedExtensions: ['nc', 'csv'],
    itemLimit: 10,
    sizeLimit: 1073741824, // 1 GB = 1014 * 1024 * 1024 bytes
  },
  callbacks: {
    onComplete: function(id, name, response) {
      //var previewLink = qq(this.getItemByFileId(id)).getByClass('preview-link')[0];
      
      if (response.success) {
        //previewLink.setAttribute("href", response.tempLink)
        //alert('success')
      }
    }
  },
});

qq(document.getElementById("btn-upload-all")).attach('click', function() {
  uploader.uploadStoredFiles();
});
