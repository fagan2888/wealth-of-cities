import sympy as sym


# define the number of cities
num_cities = 100

# define parameters
f, phi = sym.var('f, phi')
elasticity_substitution = sym.DeferredVector('theta')
economic_distance = sym.MatrixSymbol('delta', num_cities, num_cities)
labor_supply = sym.DeferredVector('S')

# define variables
nominal_gdp = sym.DeferredVector('Y')
price_level = sym.DeferredVector('P')
nominal_wage = sym.DeferredVector('W')
number_firms = sym.DeferredVector('M')


def cost(quantity, h, j):
    """Cost of a firm in city h to produce a given quantity of good j."""
    return labor_demand(quantity, h, j) * nominal_wage[h]


def goods_market_clearing(h):
    """Exports must balance imports for city h."""
    return total_exports(h) - total_imports(h)


def labor_demand(quantity, h, j):
    """Labor demand by a firm in city h to produce a given quantity of good j."""
    return (quantity / labor_productivity(h, j)) + f


def labor_market_clearing(h):
    """Labor market clearing condition for city h."""
    return labor_supply[h] - total_labor_demand(h)


def labor_productivity(h, j):
    """Productivity of labor in city h when producing good j."""
    return phi / economic_distance[h, j]


def marginal_costs(h, j):
    """Marginal costs of production of good j in city h."""
    return nominal_wage[h] / labor_productivity(h, j)


def mark_up(j):
    """Markup over marginal costs of production for good j."""
    return (elasticity_substitution[j] / (elasticity_substitution[j] - 1))


def optimal_price(h, j):
    """Optimal price of good j sold in city h."""
    return mark_up(j) * marginal_costs(h, j)


def total_profits(h):
    """Total profits for a firm in city h."""
    return total_revenue(h) - total_cost(h)


def quantity_demand(price, j):
    """Quantity demanded of a good in city j depends negatively on its price."""
    return relative_price(price, j)**(-elasticity_substitution[j]) * real_gdp(j)


def real_gdp(i):
    """Real gross domestic product of city i."""
    return nominal_gdp[i] / price_level[i]


def relative_price(price, j):
    """Relative price of a good in city j."""
    return price / price_level[j]


def resource_constraint(h):
    """Nominal GDP in city h must equal nominal income in city h."""
    return nominal_gdp[h] - labor_supply[h] * nominal_wage[h]


def revenue(price, quantity):
    """Revenue from producing a certain quantity at a given price."""
    return price * quantity


def total_cost(h):
    """Total cost of production for a firm in city h."""
    individual_costs = []
    for j in range(num_cities):
        p_star = optimal_price(h, j)
        q_star = quantity_demand(p_star, j)
        individual_costs.append(cost(q_star, h, j))

    return sum(individual_costs)


def total_exports(h):
    """Total exports of various goods from city h."""
    individual_exports = []
    for j in range(num_cities):
        p_star = optimal_price(h, j)
        q_star = quantity_demand(p_star, j)
        individual_exports.append(number_firms[h] * revenue(p_star, q_star))

    return sum(individual_exports)


def total_imports(h):
    """Total imports of various foods into city h."""
    individual_imports = []
    for j in range(num_cities):
        p_star = optimal_price(j, h)
        q_star = quantity_demand(p_star, h)
        individual_imports.append(number_firms[j] * revenue(p_star, q_star))

    return sum(individual_imports)


def total_labor_demand(h):
    """Total labor demand for a firm in city h."""
    individual_labor_demands = []
    for j in range(num_cities):
        p_star = optimal_price(h, j)
        q_star = quantity_demand(p_star, j)
        individual_labor_demands.append(labor_demand(q_star, h, j))

    return sum(individual_labor_demands)


def total_revenue(h):
    """Total revenue for a firm producing in city h."""
    individual_revenues = []
    for j in range(num_cities):
        p_star = optimal_price(h, j)
        q_star = quantity_demand(p_star, j)
        individual_revenues.append(revenue(p_star, q_star))

    return sum(individual_revenues)
