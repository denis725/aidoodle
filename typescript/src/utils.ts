
export function randChoice<T>(options: Array<T>): T {
    const idx = Math.floor(Math.random() * options.length);
    return options[idx];
};

export const sum = (arr: number[]): number => {
    return arr.reduce((x, y) => x + y, 0);
};
