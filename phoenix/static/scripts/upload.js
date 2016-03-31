$('#fine-uploader').fineUploader({
  debug: true,
  template: 'qq-template',
  request: {
    endpoint: '/upload'
  },
  thumbnails: {
    placeholders: {
      //waitingPath: '/static/jquery.fine-uploader/placeholders/waiting-generic.png',
      //notAvailablePath: '/static/jquery.fine-uploader/placeholders/not_available-generic.png',
    }
  },
  autoUpload: false,
  chunking: {
    enabled: false,
    concurrent: {
      enabled: false
    },
    //success: {
    //  endpoint: "/upload"
    //}
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
  validation: {
    allowedExtensions: ['nc', 'csv'],
    itemLimit: 10,
    sizeLimit: 1073741824, // 1 GB = 1014 * 1024 * 1024 bytes
  },
  callbacks: {
    onValidate: function(id, name) {
      console.log("onValidate");
    },
    onSubmit: function(id, name) {
      console.log("onSubmit");
    },
    onUpload: function(id, name) {
      console.log("onUpload");
    },
    onProgress: function(id, name) {
      console.log("onProgress");
    },
    onCancel: function(id, name) {
      console.log("onCancel");
    },
    onError: function(id, name) {
      console.log("onError");
    },
    onComplete: function(id, name, response) {
      console.log("onComplete");
      //var previewLink = qq(this.getItemByFileId(id)).getByClass('preview-link')[0];
      
      if (response.success) {
        //previewLink.setAttribute("href", response.tempLink)
      }
    }
  },
});

$('#trigger-upload').click(function() {
  $('#fine-uploader').fineUploader('uploadStoredFiles');
});

