If you installed this add-on before 2019-02-17 and you have updated you need to
reset the config of this add-on: In the lower left corner click the button
"Restore Defaults".

Changes of this config file require a restart of Anki.

For each action there are these options:

- `Category`: at the moment you can select between
  "forecolor","backcolor","style","class". The latter actions require a minimal
  knowledge understanding of html/css. But it's easy to modify the default
  commands with some googling. For details about "class" see below.
- `Hotkey`
- `Setting`: this value will be applied. The meaning of this value depends on
  the value of `Category`. For "forecolor" and "backcolor" add a color which
  must be in the hexadecimal format with a leading # ("#RRGGBB"). 
- `Show_in_menu`: if "true" this action is shown in a collapsible menu
- `Text_in_menu`: this text is used in the collapsible menu (if the action is
  shown in it)
- `Text_in_menu_styling`: not relevant for "forecolor" or "backcolor". This
  styling is applied to `Text_in_menu` if `v2_menu_styling` is set to "true".
- `extrabutton_show`: if "true" a separate button just for this action is shown.
  If you know the shortcut well you might not need an additional button. Or
  maybe an entry in the collapsible is enough for you.
- `extrabutton_text`: letters that will be shown on the extrabutton (only
  relevant if `extrabutton_show` is "true)  
- `extrabutton_tooltip`: tooltip for the extrabutton (only relevant if
  `extrabutton_show` is "true)
- `extrabutton_width`: at the moment this setting has no effect.


### about the categories "class"

This just applies a class. You need to set the appropriate CSS in the relevant
stylesheet. This gives you much flexibility and makes it easy to adjust the
styling for all cards you have - e.g. if you use some dark mode etc.

You need to adjust TWO style sheets:

You need to adjust the stylesheet of the **editor** with the add-on [Customize
Editor Stylesheet](https://ankiweb.net/shared/info/1215991469).

For **reviews** you need to adjust adjust the [Card
Styling](https://apps.ankiweb.net/docs/manual.html#card-styling). If you have
many card types or note types it might be easier to use one external stylesheet
that you use for each note type. You put this stylesheet in your media folder
use @import. The only content of Styling section would be e.g. `@import
url("_style.anki.main.css");` Note the leading underscore in the file name. This
is necessary to keep Anki from marking the file as unused and deleting it. for
the location of the media folder of your profile see [this
section](https://apps.ankiweb.net/docs/manual.html#file-locations) from the
manual.



