<div>
  % if content_type == 'application/directory':
  <a href="${url}" class="block"><i class="icon-inbox"></i> ${name}</a>
  % else:       
  <i class="icon-file"></i> ${name}
  % endif
</div> 
