import {Gender, GroupCategory, RelationshipStatusType} from "./Enums";
import {TimeDelta, VariableDate} from "./Utils";

export type Person = {
    id: number,
    firstName: string,
    lastName: string,
    maidenName: string,
    nickname: string,
    gender: Gender,
    birthDate: VariableDate,
    deathDate: VariableDate | null,
    age: TimeDelta,
    memberships: Array<Membership>
}

export type Relationship = {
    id: number,
    source: number,
    target: number,
    statuses: Array<RelationshipStatus>,
    duration: TimeDelta
}

export type RelationshipStatus = {
    status: RelationshipStatusType,
    dateStart: VariableDate,
    dateEnd: VariableDate | null,
    duration: TimeDelta
}

export type Membership = {
    dateStarted: VariableDate,
    dateEnded: VariableDate | null,
    duration: TimeDelta,
    groupName: string,
    groupCategory: GroupCategory
}
