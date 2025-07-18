export declare class SetValueModelFilteringKeys {
    private filteringKeys;
    private filteringKeysCaseFormatted;
    hasNoAppliedFilteringKeys: boolean;
    private readonly caseFormat;
    constructor({ caseFormat }: {
        caseFormat: <T extends string | null>(valueToFormat: T) => typeof valueToFormat;
    });
    allFilteringKeys(): Set<string | null> | null;
    allFilteringKeysCaseFormatted(): Set<string | null> | null;
    setFilteringKeys(filteringKeys: Set<string | null> | null): void;
    addFilteringKey(key: string | null): void;
    hasCaseFormattedFilteringKey(key: string | null): boolean;
    hasFilteringKey(key: string | null): boolean;
    reset(): void;
}
