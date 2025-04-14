export interface ServerResponse {
    name: string;
    recipe: string[];
    ingredients: Ingredients[];
}

interface Ingredients {
    name: string;
    img_url: string;
    price: number;
}