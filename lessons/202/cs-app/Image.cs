internal readonly struct Image
{
    public string ObjKey { get; }
    public Guid ImageUuid { get; }
    public DateTime CreatedAt { get; }

    public Image()
    {
        ImageUuid = Guid.NewGuid();
        CreatedAt = DateTime.Now;
    }

    public Image(string key) : this()
    {
        ObjKey = key;
    }
}