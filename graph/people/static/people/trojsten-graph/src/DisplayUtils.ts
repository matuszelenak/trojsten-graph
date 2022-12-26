import {GroupCategory, RelationshipStatusType} from "./Enums";
import {Person, Relationship} from "./DataTypes";
import {EdgeDisplayProps, NodeDisplayProps} from "./Graph";
import {defaultNodeColor} from "./Constants";

export function getRelationshipTypeColor(relationshipType: RelationshipStatusType): string {
    switch (relationshipType) {
        case RelationshipStatusType.BLOOD_RELATIVE:
            return '#008080';
        case RelationshipStatusType.SIBLING:
            return '#008700';
        case RelationshipStatusType.PARENT_CHILD:
            return '#8080ff';
        case RelationshipStatusType.MARRIED:
            return '#b70000';
        case RelationshipStatusType.DATING:
            return '#ffffff';
        case RelationshipStatusType.ENGAGED:
            return '#ffc000';
        case RelationshipStatusType.RUMOUR:
            return '#ff00ff';
    }
}

export function getSeminarColor(seminar: string): string {
    switch (seminar) {
        case "KSP":
            return '#818f3d';
        case "KMS":
            return '#4a6fd8';
        case "FKS":
            return '#e39f3c';
        case "Suši":
            return '#cd3c37'
    }
    return defaultNodeColor
}

export function durationToLineWidth(totalDays: number): number {
    if (totalDays < 30) {
        return 1
    }
    if (totalDays < 90) {
        return 1.5
    }
    if (totalDays < 365) {
        return 2
    }
    if (totalDays < 3 * 365) {
        return 2.5
    }
    if (totalDays < 5 * 365) {
        return 3
    }
    return 3.5
}

export function ageToRadius(years: number): number {
    if (years < 6) {
        return 5
    }
    if (years < 15) {
        return 6
    }
    if (years < 18) {
        return 7
    }
    if (years < 21) {
        return 8
    }
    if (years < 25) {
        return 9
    }
    if (years < 30) {
        return 10
    }
    return 11
}

export function getEdgeDisplayProps(relationship: Relationship): EdgeDisplayProps {
    const currentStatus = relationship.statuses[0]

    return {
        color: getRelationshipTypeColor(currentStatus.status),
        width: currentStatus.dateEnd == null ? durationToLineWidth(relationship.duration.totalDays) : 1,
        dashing: currentStatus.dateEnd === null ? [] : [2, 2]
    }
}

export function getNodeDisplayProps(person: Person): NodeDisplayProps {
    // @ts-ignore
    const seminarDurations = new Map(
        person.memberships
            .filter(m => m.groupCategory == GroupCategory.SEMINAR)
            .map(m => [m.groupName, m.duration.totalDays] as [string, number])
    )

    const totalSeminarDuration = Array.from(seminarDurations.values()).reduce((acc, val) => acc + val, 0)
    let previousAngleEnd = 0
    const pie = Array.from(seminarDurations.entries()).map(([seminar, duration]) => {
        const angleEnd = previousAngleEnd + (duration / totalSeminarDuration) * Math.PI * 2
        const pieSlice = {
            color: getSeminarColor(seminar),
            angleStart: previousAngleEnd,
            angleEnd: angleEnd
        }
        previousAngleEnd = angleEnd
        return pieSlice
    })

    return {
        isHighlighted: false,
        radius: ageToRadius(person.age.years),
        seminarPie: pie
    }
}
