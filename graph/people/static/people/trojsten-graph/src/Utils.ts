export type TimeDelta = {
    days: number,
    months: number,
    years: number,
    totalDays: number,
    isPrecise: boolean
}

export type VariableDate = {
    year: number,
    month: number | null,
    day: number | null
}

export function isExactDate(date: VariableDate): boolean {
    return date.day !== null && date.month !== null
}

export function toRegularDate(date: VariableDate | null): Date {
    if (date !== null){
        const complete = {
            year: date.year,
            month: date.month ?? 1,
            day: date.day ?? 1
        }
        return new Date(`${complete.year}-${complete.month}-${complete.day}`)
    }
    return new Date()
}

export function normalizeString(str: string | null) {
    return str?.normalize('NFKD')?.replace(/[\u0300-\u036F]/g, '')
}

// point - { x, y }
// line - { sx, sy, ex, ey }
export type Line = {
    sx: number
    sy: number
    ex: number
    ey: number
}

export type Point = {
    x: number
    y: number
}

export function distToSegment(point: Point, line: Line): number
{
    const dx = line.ex - line.sx;
    const dy = line.ey - line.sy;
    const l2 = dx * dx + dy * dy;

    if (l2 == 0)
        return dist(point, line.sx, line.sy);

    let t = ((point.x - line.sx) * dx + (point.y - line.sy) * dy) / l2;
    t = Math.max(0, Math.min(1, t));

    return dist(point, line.sx + t * dx, line.sy + t * dy);
}

function dist(point: Point, x: number, y: number): number
{
    const dx = x - point.x;
    const dy = y - point.y;
    return Math.sqrt(dx * dx + dy * dy);
}