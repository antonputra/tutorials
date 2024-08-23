internal readonly struct Device
{
    public string Uuid { get; }
    public string Mac { get; }
    public string Firmware { get; }

    public Device(string uuid, string mac, string firmware)
    {
        Uuid = uuid;
        Mac = mac;
        Firmware = firmware;
    }
}
