-- __MOD_NAME__
-- Entry point loaded by Steamodded (see manifest.json -> main_file)

local mod = SMODS.current_mod

-- Example: an atlas for your joker sprites.
-- Put a 71x95-per-card PNG at assets/1x/jokers.png and a 142x190 version at assets/2x/jokers.png
-- SMODS.Atlas {
--     key = "jokers",
--     path = "jokers.png",
--     px = 71,
--     py = 95,
-- }

-- Example joker:
-- SMODS.Joker {
--     key = "example",
--     loc_txt = {
--         name = "Example Joker",
--         text = { "{C:mult}+#1#{} Mult" },
--     },
--     config = { extra = { mult = 4 } },
--     rarity = 1,
--     cost = 4,
--     atlas = "jokers",
--     pos = { x = 0, y = 0 },
--     loc_vars = function(self, info_queue, card)
--         return { vars = { card.ability.extra.mult } }
--     end,
--     calculate = function(self, card, context)
--         if context.joker_main then
--             return { mult = card.ability.extra.mult }
--         end
--     end,
-- }

sendInfoMessage("__MOD_NAME__ loaded", "__MOD_ID__")
