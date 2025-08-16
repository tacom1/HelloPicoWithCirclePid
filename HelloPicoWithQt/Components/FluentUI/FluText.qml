import QtQuick
import QtQuick.Controls

// https://github.com/zhuzichu520/FluentUI/blob/main/src/Qt6/imports/FluentUI/Controls/FluText.qml
Text {
    property color textColor: Qt.rgba(7/255, 7/255, 7/255, 1)
    id: text
    color: enabled ? textColor : Qt.rgba(160/255,160/255,160/255,1)
    // renderType: FluTheme.nativeText ? Text.NativeRendering : Text.QtRendering
    font {
        pixelSize: 13
    }
}
