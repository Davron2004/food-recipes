export interface Recipe {
    id: number;
    name: string;
    instructions: string;
    category: Category;
    ingredients: IngRec[];
    pictures: string[];
}

export interface RecipeExtended extends Recipe {
    id: number;
    name: string;
    instructions: string;
    category: Category;
    ingredients: IngRec[];
    pictures: string[];

    needs_auth: boolean;
    created_at: string;
    updated_at: string;
}

export interface IngRec {
    ingredient: Ingredient;
    qty: number;
    unit: 'pinch' | 'kg' | 'gram' | 'ml' | 'liter' | 'cup';
}

export interface Category {
    id: number;
    name: string;
}

export interface Ingredient {
    id: number;
    name: string;
}