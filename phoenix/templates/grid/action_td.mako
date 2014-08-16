<div class="dropdown">
  % if len(buttongroup) > 0:
  <a class="dropdown-toggle" data-toggle="dropdown" href="#"><div display="inline-block"><i class="icon-cog"></i> actions<b class="caret"></b></div></a>
  <ul class="dropdown-menu" role="menu" aria-labelledby="dLabel">
    <!-- dropdown menu links -->
    % for name,value,icon,title in buttongroup:
    <li><a class="${name}" data-value="${value}"><i class="${icon}"></i> ${title}</a></li>
    % endfor
  </ul>
  % endif
</div>
