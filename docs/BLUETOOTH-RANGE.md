# Bluetooth link stability

Bluetooth reception has limited link margin in the tested V3 Blaze, particularly with sustained high-bitrate LDAC and difficult RF conditions. Higher rates produced repeated dropouts; lower-rate LDAC also cut out in crowded wireless environments. AAC was more reliable in the tested normal-use scenarios.

The [v1.3 Bluetooth Receiver LDAC audio corruption](LDAC-RECEIVER-ARTIFACTS.md) occurred with continuous packet reception and was corrected by the decoder patch. Link dropouts are a separate symptom. The exact RF-level cause has not been established.

Wi-Fi range also appeared poor in similar conditions. The Broadcom combo platform handles both radios, but these observations do not identify the underlying RF cause.

Neither edition includes an RF fix. These observations concern the tested unit and conditions.
