import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Basic

Button {
    display: Button.IconOnly
    property int iconSize: 20
    property int iconSource
    property bool disabled: false
    property int radius: 4
    property string contentDescription: ""
    property color hoverColor: Qt.rgba(0, 0, 0, Math.round(255 * 0.1) / 255)
    property color pressedColor: Qt.rgba(0, 0, 0, Math.round(255 * 0.08) / 255)
    property color normalColor: Qt.rgba(0, 0, 0, 0)
    property color disableColor: Qt.rgba(0, 0, 0, 0)
    property Component iconDelegate: com_icon
    property color color: {
        if(!enabled){
            return disableColor
        }
        if(pressed){
            return pressedColor
        }
        return hovered ? hoverColor : normalColor
    }
    property color iconColor: {
        if(!enabled){
            return Qt.rgba(161/255,161/255,161/255,1)
        }
        return Qt.rgba(0,0,0,1)
    }
    property color textColor: {
        if(!enabled){
            return Qt.rgba(161/255,161/255,161/255,1)
        }
        return Qt.rgba(0,0,0,1)
    }
    Accessible.role: Accessible.Button
    Accessible.name: control.text
    Accessible.description: contentDescription
    Accessible.onPressAction: control.clicked()
    id:control
    focusPolicy:Qt.TabFocus
    padding: 0
    verticalPadding: 8
    horizontalPadding: 8
    enabled: !disabled
    font.pixelSize: 12
    background: Rectangle{
        implicitWidth: 56
        implicitHeight: 56
        radius: control.radius
        color:control.color
        FluFocusRectangle{
            visible: control.activeFocus
        }
        // Rectangle{
        //     visible: control.activeFocus
        //     anchors.fill: parent
        //     color: Qt.rgba(35/255, 161/255, 159/255, 1)
        //     border.width: 2
        //     radius: 4
        //     border.color: Qt.rgba(0,0,0,1)
        //     z: 65535
        // }
    }
    Component{
        id:com_icon
        FluIcon {
            id:text_icon
            font.pixelSize: iconSize
            iconSize: control.iconSize
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            iconColor: control.iconColor
            iconSource: control.iconSource
        }
    }
    Component{
        id:com_row
        RowLayout{
            Loader {
                sourceComponent: iconDelegate
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                visible: display !== Button.TextOnly
            }
            FluText{
                text:control.text
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                visible: display !== Button.IconOnly
                color: control.textColor
                font: control.font
            }
        }
    }
    Component{
        id:com_column
        ColumnLayout{
            Loader {
                sourceComponent: iconDelegate
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                visible: display !== Button.TextOnly
            }
            FluText{
                text:control.text
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                visible: display !== Button.IconOnly
                color: control.textColor
                font: control.font
            }
        }
    }
    contentItem:Loader {
        sourceComponent: {
            if(display === Button.TextUnderIcon){
                return com_column
            }
            return com_row
        }
    }
    FluTooltip{
        id:tool_tip
        visible: {
            if(control.text === ""){
                return false
            }
            if(control.display !== Button.IconOnly){
                return false
            }
            return hovered
        }
        text:control.text
        delay: 1000
    }
}
