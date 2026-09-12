///////////////////////////
// DoDA/WeaponSystem/DetachableMagazineState.zs
///////////////////////////

// Shared state contract and operations for detachable-magazine firearms with closed-bolt +1 chambering (B92, MP5).
struct DoDADetachableMagState
{
    int magazineRounds;
    bool chamberLoaded;
    bool initialized;

    void Initialize(int capacity, bool chamber = true)
    {
        if (initialized)
        {
            return;
        }

        magazineRounds = capacity;
        chamberLoaded = chamber;
        initialized = true;
    }

    clearscope int GetLoadedRoundCount() const
    {
        return magazineRounds + (chamberLoaded ? 1 : 0);
    }

    clearscope bool IsEmpty() const
    {
        return !chamberLoaded && magazineRounds == 0;
    }

    clearscope bool CanFireRound() const
    {
        return chamberLoaded;
    }

    bool ConsumeFiredRound()
    {
        if (!chamberLoaded)
        {
            return false;
        }

        chamberLoaded = false;

        if (magazineRounds > 0)
        {
            magazineRounds--;
            chamberLoaded = true;
        }

        return true;
    }

    void ChamberFromMagazine()
    {
        if (!chamberLoaded && magazineRounds > 0)
        {
            magazineRounds--;
            chamberLoaded = true;
        }
    }

    bool CanReload(int capacity, int reserveAmount) const
    {
        return magazineRounds < capacity && reserveAmount > 0;
    }

    // Replacement reload (B92 style): returns remaining mag rounds to reserve, draws full mag from reserve, chambers 1st round if empty.
    bool CommitReplacementReload(int capacity, out int reserveAmount)
    {
        if (reserveAmount <= 0 || magazineRounds >= capacity)
        {
            return false;
        }

        reserveAmount += magazineRounds;
        magazineRounds = 0;

        int roundsToLoad = Min(capacity, reserveAmount);
        magazineRounds = roundsToLoad;
        reserveAmount -= roundsToLoad;

        if (!chamberLoaded && magazineRounds > 0)
        {
            magazineRounds--;
            chamberLoaded = true;
        }

        return true;
    }

    // Top-off reload transfer (MP5 style): transfers missing rounds to magazine from reserve without disturbing chambered round.
    int PerformTopOffTransfer(int capacity, int reserveAmount)
    {
        if (reserveAmount <= 0 || magazineRounds >= capacity)
        {
            return 0;
        }

        int needed = capacity - magazineRounds;
        int transferAmount = Min(needed, reserveAmount);

        magazineRounds += transferAmount;
        return transferAmount;
    }
}
