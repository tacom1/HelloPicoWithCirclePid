import QtQuick
import QtQuick.Controls
// https://learn.microsoft.com/zh-cn/windows/apps/design/style/segoe-fluent-icons-font
Text {
    property int iconSource
    property int iconSize: 20
    property color iconColor: {
        if(!enabled){
            return Qt.rgba(161/255,161/255,161/255,1)
        }
        return Qt.rgba(0,0,0,1)
    }
    id:control
    font.family: font_loader.name
    font.pixelSize: iconSize
    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter
    color: iconColor
    text: (String.fromCharCode(iconSource).toString(16))
    opacity: iconSource>0
    FontLoader{
        id: font_loader
        source: "FluentIcons.ttf"
    }
}
