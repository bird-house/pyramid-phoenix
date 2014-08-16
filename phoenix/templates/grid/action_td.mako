<span class="dropdown">
  <a class="dropdown-toggle" data-toggle="dropdown" href="#"><i class="icon-cog"></i> actions<b class="caret"></b></a>
  <ul class="dropdown-menu">
    <!-- dropdown menu links -->
    % for name,value,icon,title in buttongroup:
    <li><a class="${name}" data-value="${value}"><i class="${icon}"></i> ${title}</a></li>
    % endfor
  </ul>
</span>
