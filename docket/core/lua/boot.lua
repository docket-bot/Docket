--this code was provided by the developer of cleanerbot.xyz, with permission
local debug_sethook = debug.sethook
local coroutine = coroutine
local error = error
local setmetatable = setmetatable
local unpack = unpack or table.unpack
local script, cycle_limit
local load = load
local pairs = pairs
local type = type
_G.load = function(chunk, chunkname, mode, env)
    if mode ~= "t" then return nil, "mode must be 't'" end
    return load(chunk, chunkname, "t", env)
end
local function safe_call(fn, ...)
    if cycle_limit == nil then
        error("no cycle limit, call set_cycle_limit")
    end
    local coro = coroutine.create(fn)
    local limit_exceeded = false
    debug_sethook(coro, function()
        limit_exceeded = true
        debug_sethook(function() error("reached cycle limit") end, "cr", 1)
        error("reached cycle limit")
    end, "", cycle_limit)
    local result = {coroutine.resume(coro, ...)}
    if limit_exceeded then
        error("reached cycle limit")
    end
    for _, v in pairs(result) do
        if type(v) == "table" then
            setmetatable(v, {})
        end
    end
    if not result[1] then
        error(unpack(result, 2))
    end
    return unpack(result, 2)
end
return {
    set_cycle_limit = function(limit)
        cycle_limit = limit
    end,
    set_script = function(source)
        local fn, err = load(source, "<worker>", "t")
        if fn == nil then
            error(err)
        end
        script = safe_call(fn)
    end,
    call = function(...)
        return safe_call(script, ...)
    end,
}
