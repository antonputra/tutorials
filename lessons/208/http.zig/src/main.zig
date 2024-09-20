const std = @import("std");
const httpz = @import("httpz");
const builtin = @import("builtin");
const Device = @import("device.zig");

const port = 8080;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const allocator = gpa.allocator();

    // If you want to use c_allocator - im not seeing any real difference in speed with this though
    // var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    // const allocator = if (builtin.mode == .Debug) gpa.allocator() else blk: {
    //     std.debug.print("Using Raw OS allocator\n", .{});
    //     break :blk std.heap.raw_c_allocator;
    // };

    defer if (builtin.mode == .Debug) {
        _ = gpa.detectLeaks();
    };

    var app = App{};

    // playing around with fine tuning params to match what the prod system looks like
    // with is 2 vCPUs ?
    //
    // This should consume around 2MB memory in total for sustained hits
    var server = try httpz.Server(*App).init(allocator, .{
        .address = "0.0.0.0",
        .port = port,
        .workers = .{
            .count = 2,
            .max_conn = 8 * 1024,
            // .max_conn = 1024, // default 500
            // .large_buffer_count = 1,
            .large_buffer_count = 0,
            // .large_buffer_size = 1024,
        },
        .thread_pool = .{
            .count = 2,
            .buffer_size = 64 * 1024,
        },
        .request = .{
            .buffer_size = 1024,
            .max_header_count = 0,
            .max_param_count = 0,
            .max_query_count = 0,
            .max_form_count = 0,
            .max_multiform_count = 0,
        },
    }, &app);
    var router = server.router(.{});
    router.get("/healthz", App.healthz, .{});
    router.get("/api/devices", App.getDevices, .{});

    // std.debug.print("http.zig (max_conn_handling branch) listening on http://0.0.0.0:{d}\n", .{port});
    std.debug.print("http.zig (tweaks branch) listening on http://0.0.0.0:{d}\n", .{port});
    try server.listen();
}

const App = struct {
    fn healthz(_: *App, _: *httpz.Request, res: *httpz.Response) !void {
        res.body = "OK";
    }

    fn getDevices(_: *App, _: *httpz.Request, res: *httpz.Response) !void {
        try res.json([_]Device{Device{
            .id = 1,
            .mac = "EF-2B-C4-F5-D6-34",
            .firmware = "2.1.5",
        }}, .{});
    }
};
