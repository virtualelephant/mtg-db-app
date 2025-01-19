DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'mtg_cards'
    ) THEN
        CREATE TABLE mtg_cards (
            id SERIAL PRIMARY KEY,
            name TEXT,
            multiverse_id BIGINT,
            layout TEXT,
            names TEXT[], -- Array of alternative card names
            mana_cost TEXT,
            cmc NUMERIC,
            colors TEXT[],
            color_identity TEXT[],
            type TEXT,
            supertypes TEXT[],
            subtypes TEXT[],
            rarity TEXT,
            text TEXT,
            flavor TEXT,
            artist TEXT,
            number TEXT,
            power TEXT,
            toughness TEXT,
            loyalty TEXT,
            variations TEXT[],
            watermark TEXT,
            border TEXT,
            timeshifted BOOLEAN,
            hand INTEGER,
            life INTEGER,
            reserved BOOLEAN,
            release_date DATE,
            starter BOOLEAN,
            rulings JSONB,
            foreign_names JSONB,
            printings TEXT[],
            original_text TEXT,
            original_type TEXT,
            legalities JSONB,
            source TEXT,
            image_url TEXT,
            sets TEXT[],
            set_name TEXT[]
        );
    END IF;
END $$;

-- Create a new table for MTG sets
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'mtg_sets'
    ) THEN
        CREATE TABLE mtg_sets (
            id SERIAL PRIMARY KEY,
            set_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            release_date DATE,
            total_cards INTEGER
        );
    END IF;
END $$;
