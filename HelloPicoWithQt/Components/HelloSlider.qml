import QtQuick
import "./FluentUI"

FluSlider{
    id: root
    tooltipEnabled: false
    from: -30000
    to: 50000
    stepSize: 0.01

    FluText{
        id: leftText
        text: String(root.from)
        anchors{
            left: parent.left
            leftMargin: -80
            verticalCenter: parent.verticalCenter
        }
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    FluText{
        id: rightText
        text: String(root.to)
        anchors{
            right: parent.right
            rightMargin: -70
            verticalCenter: parent.verticalCenter
        }
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    FluText{
        id: topText
        text: String(root.value.toFixed(2))
        anchors{
            top: parent.top
            topMargin: -20
            horizontalCenter: parent.horizontalCenter
        }
        font.pixelSize: 18
        color: "#3b4a5a"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
