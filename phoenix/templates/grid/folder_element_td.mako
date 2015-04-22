<div>
  <div> 
    % if content_type == 'application/directory':
    <strong><a href="${url}" class="block"><i class="icon-inbox"></i> ${name}</a></strong>
    % else:       
    <b><i class="icon-file"></i> ${name}</b>
    % endif
  </div>
</div> 
