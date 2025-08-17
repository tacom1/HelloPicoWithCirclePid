import QtQuick
import "./FluentUI"

FluSlider{
    property bool needMM: true
    property int leftTextMargin: -80
    property int rightTextMargin: -60
    id: root
    tooltipEnabled: false
    from: -30000
    to: 50000
    stepSize: 0.01

    FluText{
        id: topText
        text: String(root.value.toFixed(2)) + (needMM ? "mm" : "")
        anchors{
            top: parent.top
            topMargin: -60
            left: parent.left
        }
        font.pixelSize: 32
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
