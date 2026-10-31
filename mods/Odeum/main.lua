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

-- Every pack's tracks are registered up front. The game plays all "music" sounds
-- in sync and fades between them, so switching packs or slots is seamless.
for _, id in ipairs(Odeum.order) do
    local pack = Odeum.packs[id]
    for slot = 1, SLOTS do
        if pack.tracks[slot] then
            local sound = SMODS.Sound {
                key = id .. "_music" .. slot,
                -- SMODS resolves paths from assets/sounds/
                path = "../../packs/" .. id .. "/music/music" .. slot .. ".ogg",
                volume = pack.volume,
                pitch = pack.pitch,
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

G.FUNCS.odeum_select_pack = function(e)
    mod.config.pack = e.cycle_config.odeum_ids[e.to_key]
    SMODS.save_mod_config(mod)
    Odeum.refresh_title()
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

    return {
        n = G.UIT.ROOT,
        config = { align = "cm", padding = 0.2, colour = G.C.BLACK, r = 0.1, minw = 8 },
        nodes = {
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
        },
    }
end

log(("Loaded %d pack(s); active: %s"):format(#Odeum.order, mod.config.pack))
