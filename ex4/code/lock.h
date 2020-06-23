#ifndef LOCK_H_
#define LOCK_H_

typedef volatile int spinlock_t;

#define UNLOCKED  0 
#define LOCKED    1

/*  
    Implementation basd on following resources:
    Resource 1: http://www.cs.cornell.edu/courses/cs4410/2015su/lectures/lec06-spin.html
    Resource 2: https://en.wikipedia.org/wiki/Test_and_test-and-set
*/

static inline void spin_lock_init(spinlock_t *spin_var)
{
    *spin_var = UNLOCKED; 
}

static inline void spin_lock_tas_cas(spinlock_t *spin_var)
{
    while (__sync_val_compare_and_swap(spin_var, 0, 1));
}

static inline void spin_lock_ttas_cas(spinlock_t *spin_var)
{
    do {
        while (*spin_var == LOCKED);
    } while (__sync_val_compare_and_swap(spin_var, 0, 1));
}

static inline void spin_lock_tas_ts(spinlock_t *spin_var)
{
    while (__sync_lock_test_and_set(spin_var, 1));
}

static inline void spin_lock_ttas_ts(spinlock_t *spin_var)
{
    do {
        while (*spin_var == LOCKED);
    } while (__sync_lock_test_and_set(spin_var, 1));
}

static inline void spin_unlock(spinlock_t *spin_var)
{
    __sync_lock_release(spin_var);
}


#endif
