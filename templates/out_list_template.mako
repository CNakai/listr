<!DOCTYPE html>
<html>
    <head>
        <title>Listr</title>
        <style>
         <%include file="out_list_style.css"/>
        </style>
    </head>

    <body>

    % for listing in listings:
        <div data-name="${listing['name']}" data-set="${listing['set']}">
      % if listing['sort_type'] == 'SRCNO':
          <input type="checkbox"> | <span class="set">${listing['set']}</span> |
          <span class="rarity">${listing['rarity']}</span> |
          <span class="color">${listing['color']}</span> |
          <span class="name">${listing['name']}</span>
      % else:
          <input type="checkbox"> |
          <span class="color">${listing['color']}</span> |
          <span class="name">${listing['name']}</span>
      % endif
        </div>
    % endfor

    <%include file="out_list_scripts.mako"/>

    </body>
</html>
