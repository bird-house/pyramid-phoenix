<div>
  <div> 
    % if content_type == 'application/directory':
    <strong><a href="${url}" class="block">${name}</a></strong>
    % else:       
    <b>${name}</b>
    % endif
  </div>
</div> 
