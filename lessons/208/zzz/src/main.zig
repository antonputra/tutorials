const std = @import("std");
const zzz = @import("zzz");
const http = zzz.HTTP;

pub const std_options = .{
    .log_level = .err,
};

const Device = struct {
    id: i32,
    mac: []const u8,
    firmware: []const u8,
};

fn healthz_handler(_: http.Request, response: *http.Response, _: http.Context) void {
    response.set(.{
        .status = .OK,
        .mime = http.Mime.HTML,
        .body = "OK",
    });
}

fn devices_handler(_: http.Request, response: *http.Response, ctx: http.Context) void {
    const device = comptime Device{
        .id = 1,
        .mac = "EF-2B-C4-F5-D6-34",
        .firmware = "2.1.5",
    };

    const json = std.json.stringifyAlloc(ctx.allocator, device, .{}) catch "";

    response.set(.{
        .status = .OK,
        .mime = http.Mime.JSON,
        .body = json,
    });
}

pub fn main() !void {
    const allocator = std.heap.c_allocator;

    var router = http.Router.init(allocator);
    defer router.deinit();

    try router.serve_route("/healthz", http.Route.init().get(healthz_handler));
    try router.serve_route("/api/devices", http.Route.init().get(devices_handler));

    var server = http.Server(.plain).init(.{
        .allocator = allocator,
        .threading = .{ .multi_threaded = .{ .count = 2 } },
        .size_socket_buffer = 256,
        .size_completions_reap_max = 256,
        // This is how many connections each thread can handle.
        // Needs to be a power of 2.
        .size_connections_max = 4096,
    }, .io_uring);
    defer server.deinit();

    try server.bind("0.0.0.0", 8080);
    try server.listen(.{
        .router = &router,
        .num_header_max = 16,
        .num_captures_max = 0,
    });
}
