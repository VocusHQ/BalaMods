-- Odeum
-- Soundtrack packs for Balatro. Each folder in packs/ is one pack: a song in five
-- synced variants (music1..music5), plus optionally its own title logo.
-- The active pack is picked in the mod's config tab.

local mod = SMODS.current_mod

Odeum = {
    mod = mod,
    packs = {},     -- id -> pack
    order = {},     -- pack ids, sorted by display name
}

-- Vanilla music slots, in the order the game checks them (see modulate_sound)
local SLOTS = 5
local LOGO_W, LOGO_H = 333, 216

local function log(msg) sendInfoMessage(msg, "Odeum") end
local function warn(msg) sendWarnMessage(msg, "Odeum") end

local function exists(path) return NFS.getInfo(path) ~= nil end

--------------------------------------------------------------------------------
-- Pack discovery
--------------------------------------------------------------------------------

local function load_pack(id)
    local dir = mod.path .. "packs/" .. id .. "/"
    if not exists(dir .. "pack.lua") then return end

    local ok, def = pcall(function()
        return assert(load(NFS.read(dir .. "pack.lua"), "=[Odeum pack " .. id .. "]"))()
    end)
    if not ok or type(def) ~= "table" then
        warn(("Pack '%s': could not read pack.lua (%s)"):format(id, tostring(def)))
        return
    end

    local pack = {
        id = id,
        dir = dir,
        name = def.name or id,
        author = def.author,
        description = def.description,
        volume = def.volume or 0.6,
        pitch = def.pitch or 1,
        card = def.card,
        tracks = {}, -- slot -> SMODS sound key
    }

    for slot = 1, SLOTS do
        if exists(dir .. "music/music" .. slot .. ".ogg") then
            pack.tracks[slot] = true
        end
    end
    if not pack.tracks[1] then
        warn(("Pack '%s': missing music/music1.ogg, skipped"):format(id))
        return
    end

    pack.has_title = exists(dir .. "title.png")
    return pack
end

for _, id in ipairs(NFS.getDirectoryItems(mod.path .. "packs")) do
    local pack = load_pack(id)
    if pack then
        Odeum.packs[id] = pack
        Odeum.order[#Odeum.order + 1] = id
    end
end
table.sort(Odeum.order, function(a, b) return Odeum.packs[a].name < Odeum.packs[b].name end)

function Odeum.active_pack()
    return Odeum.packs[mod.config.pack]
end

--------------------------------------------------------------------------------
-- Music
--------------------------------------------------------------------------------

-- Which vanilla track (1..5) the game wants right now. Mirrors modulate_sound.
function Odeum.current_slot()
    if G.booster_pack_sparkles and not G.booster_pack_sparkles.REMOVED then return 2 end
    if G.booster_pack_meteors and not G.booster_pack_meteors.REMOVED then return 3 end
    if G.booster_pack and not G.booster_pack.REMOVED then return 2 end
    if G.shop and not G.shop.REMOVED then return 4 end
    if G.GAME and G.GAME.blind and G.GAME.blind.boss then return 5 end
    return 1
end

-- Player settings per pack, as percentages of the pack's own volume and speed
function Odeum.settings(pack)
    mod.config.settings = mod.config.settings or {}
    local s = mod.config.settings[pack.id]
    if not s then
        s = { volume = 100, speed = 100 }
        mod.config.settings[pack.id] = s
    end
    return s
end

local function playback(pack)
    local s = Odeum.settings(pack)
    return pack.volume * s.volume / 100, pack.pitch * s.speed / 100
end

-- Every pack's tracks are registered up front. The game plays all "music" sounds
-- in sync and fades between them, so switching packs or slots is seamless.
for _, id in ipairs(Odeum.order) do
    local pack = Odeum.packs[id]
    local volume, pitch = playback(pack)
    for slot = 1, SLOTS do
        if pack.tracks[slot] then
            local sound = SMODS.Sound {
                key = id .. "_music" .. slot,
                -- SMODS resolves paths from assets/sounds/
                path = "../../packs/" .. id .. "/music/music" .. slot .. ".ogg",
                volume = volume,
                pitch = pitch,
                select_music_track = function()
                    if Odeum.active_pack() ~= pack then return end
                    local want = Odeum.current_slot()
                    if not pack.tracks[want] then want = 1 end -- missing variant: stay on the main song
                    if want == slot then return 0 end
                end,
            }
            pack.tracks[slot] = sound and sound.key or nil
        end
    end
end

-- Volume and speed are baked into the sound thread's sources, so changing them means
-- re-sending the pack's tracks. The music restarts from the top, still in sync.
function Odeum.apply_settings(pack)
    local volume, pitch = playback(pack)
    G.SOUND_MANAGER.channel:push({ type = "stop" })
    for _, key in pairs(pack.tracks) do
        local sound = SMODS.Sounds[key]
        if sound and sound.data then
            sound.volume, sound.pitch = volume, pitch
            G.SOUND_MANAGER.channel:push({
                type = "sound_source", sound_code = sound.sound_code, data = sound.data,
                should_stream = sound.should_stream, per = pitch, vol = volume,
            })
        end
    end
end

-- Sliders fire on every frame of a drag, so apply once the player lets go
local APPLY_DELAY = 0.4
local update_ref = Game.update
function Game:update(dt)
    update_ref(self, dt)
    if Odeum.apply_at and love.timer.getTime() >= Odeum.apply_at then
        Odeum.apply_at = nil
        local pack = Odeum.active_pack()
        if pack then
            local s = Odeum.settings(pack)
            s.volume, s.speed = math.floor(s.volume + 0.5), math.floor(s.speed + 0.5)
            Odeum.apply_settings(pack)
        end
        SMODS.save_mod_config(mod)
    end
end

--------------------------------------------------------------------------------
-- Title logo
--------------------------------------------------------------------------------

-- title.png is drawn at LOGO_W x LOGO_H; a 2x image (666x432) is recommended.
local function title_atlas(pack)
    if not pack or not pack.has_title then return end
    if pack.atlas then return pack.atlas end

    local ok, err = pcall(function()
        local data = love.image.newImageData(NFS.newFileData(pack.dir .. "title.png"))
        local w, h = data:getDimensions()
        local scale = w / LOGO_W
        local image = love.graphics.newImage(data, { mipmaps = true, dpiscale = scale })
        local mipmap_level = SMODS.config.graphics_mipmap_level_options[SMODS.config.graphics_mipmap_level]
        if mipmap_level and mipmap_level > 0 then image:setMipmapFilter("linear", mipmap_level) end

        local name = "odeum_title_" .. pack.id
        pack.atlas = { name = name, image = image, px = LOGO_W, py = math.floor(h / scale + 0.5) }
        G.ASSET_ATLAS[name] = pack.atlas -- so Sprite:reset() can find it again
    end)
    if not ok then
        warn(("Pack '%s': could not load title.png (%s)"):format(pack.id, tostring(err)))
        pack.has_title = false
    end
    return pack.atlas
end

local function title_card(pack)
    return pack and pack.card and G.P_CARDS[pack.card] or G.P_CARDS.S_A
end

-- Swap the logo (and the card in its middle) on a title screen that is already up.
function Odeum.refresh_title()
    local pack = Odeum.active_pack()
    if G.SPLASH_LOGO then
        G.SPLASH_LOGO.atlas = title_atlas(pack) or G.ASSET_ATLAS.balatro
        G.SPLASH_LOGO:set_sprite_pos({ x = 0, y = 0 })
    end
    local card = G.title_top and G.title_top.cards[1]
    if card and card.base and card.config.card ~= title_card(pack) then
        card:set_base(title_card(pack))
    end
end

local main_menu_ref = Game.main_menu
function Game:main_menu(...)
    local pack = Odeum.active_pack()
    local atlas = title_atlas(pack)
    local vanilla = G.ASSET_ATLAS.balatro
    if atlas then G.ASSET_ATLAS.balatro = atlas end
    local ok, ret = pcall(main_menu_ref, self, ...)
    G.ASSET_ATLAS.balatro = vanilla
    if not ok then error(ret, 0) end
    Odeum.refresh_title()
    return ret
end

--------------------------------------------------------------------------------
-- Config tab
--------------------------------------------------------------------------------

-- Rebuild the config tab, so the sliders show the newly selected pack
local function reopen_config()
    G.E_MANAGER:add_event(Event({
        func = function()
            G.FUNCS["openModUI_" .. mod.id]()
            return true
        end,
    }))
end

G.FUNCS.odeum_select_pack = function(e)
    mod.config.pack = e.cycle_config.odeum_ids[e.to_key]
    SMODS.save_mod_config(mod)
    Odeum.refresh_title()
    reopen_config()
end

G.FUNCS.odeum_setting_changed = function()
    Odeum.apply_at = love.timer.getTime() + APPLY_DELAY
end

G.FUNCS.odeum_reset = function()
    local pack = Odeum.active_pack()
    if not pack then return end
    local s = Odeum.settings(pack)
    s.volume, s.speed = 100, 100
    Odeum.apply_at = love.timer.getTime()
    reopen_config()
end

local function text_row(text, scale, colour)
    return {
        n = G.UIT.R, config = { align = "cm", padding = 0.02 },
        nodes = { { n = G.UIT.T, config = { text = text, scale = scale, colour = colour or G.C.UI.TEXT_LIGHT } } },
    }
end

local function pack_settings(pack)
    local s = Odeum.settings(pack)
    local nodes = {}
    if pack.description then nodes[#nodes + 1] = text_row(pack.description, 0.35) end
    if pack.author then nodes[#nodes + 1] = text_row("by " .. pack.author, 0.3, G.C.UI.TEXT_INACTIVE) end
    nodes[#nodes + 1] = create_slider {
        label = "Volume %", ref_table = s, ref_value = "volume", min = 0, max = 150,
        w = 4, h = 0.4, label_scale = 0.4, text_scale = 0.3, callback = "odeum_setting_changed",
    }
    nodes[#nodes + 1] = create_slider {
        label = "Speed %", ref_table = s, ref_value = "speed", min = 50, max = 150,
        w = 4, h = 0.4, label_scale = 0.4, text_scale = 0.3, callback = "odeum_setting_changed",
    }
    nodes[#nodes + 1] = text_row("Speed also changes pitch, like a record player.", 0.28, G.C.UI.TEXT_INACTIVE)
    nodes[#nodes + 1] = {
        n = G.UIT.R, config = { align = "cm", padding = 0.1 },
        nodes = { UIBox_button { label = { "Reset" }, button = "odeum_reset", minw = 2, minh = 0.5, scale = 0.35, colour = G.C.RED } },
    }
    return { n = G.UIT.R, config = { align = "cm", padding = 0.05 }, nodes = { { n = G.UIT.C, config = { align = "cm" }, nodes = nodes } } }
end

mod.config_tab = function()
    local ids, names, current = { "vanilla" }, { "Vanilla" }, 1
    for _, id in ipairs(Odeum.order) do
        ids[#ids + 1] = id
        names[#names + 1] = Odeum.packs[id].name
        if id == mod.config.pack then current = #ids end
    end

    local pack = Odeum.active_pack()
    local info = { "Each pack brings its own music and title." }
    if #Odeum.order == 0 then info = { "No packs found in Odeum/packs/" } end

    local nodes = {
        create_option_cycle {
            label = "Soundtrack",
            options = names,
            current_option = current,
            opt_callback = "odeum_select_pack",
            odeum_ids = ids,
            w = 5,
            scale = 0.9,
            colour = G.C.RED,
            info = info,
        },
    }
    if pack then nodes[#nodes + 1] = pack_settings(pack) end

    return {
        n = G.UIT.ROOT,
        config = { align = "cm", padding = 0.2, colour = G.C.BLACK, r = 0.1, minw = 8 },
        nodes = { { n = G.UIT.C, config = { align = "cm" }, nodes = nodes } },
    }
end

log(("Loaded %d pack(s); active: %s"):format(#Odeum.order, mod.config.pack))
