import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Basic

Button {
    property bool disabled: false
    property string contentDescription: ""
    property color normalColor: Qt.rgba(254/255,254/255,254/255,1)
    property color hoverColor: Qt.lighter(normalColor,1.1)
    property color disableColor: Qt.rgba(199/255,199/255,199/255,1)
    property color pressedColor: Qt.lighter(normalColor,1.2)
    property color textColor: {
        return Qt.rgba(1,1,1,1)
    }
    Accessible.role: Accessible.Button
    Accessible.name: control.text
    Accessible.description: contentDescription
    Accessible.onPressAction: control.clicked()
    id: control
    enabled: !disabled
    focusPolicy: Qt.TabFocus
    font {
        pixelSize: 13
    }
    verticalPadding: 0
    horizontalPadding:12
    background: FluControlBackground{
        implicitWidth: 30
        implicitHeight: 30
        radius: 4
        bottomMargin: enabled ? 2 : 0
        border.width: enabled ? 1 : 0
        border.color: enabled ? Qt.darker(control.normalColor,1.2) : disableColor
        color:{
            if(!enabled){
                return disableColor
            }
            if(pressed){
                return pressedColor
            }
            return hovered ? hoverColor :normalColor
        }
        FluFocusRectangle{
            visible: control.visualFocus
            radius:4
        }
    }
    contentItem: FluText {
        text: control.text
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: control.textColor
    }
}
